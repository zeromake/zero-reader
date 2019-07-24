package epub

import (
	gozip "archive/zip"
	"github.com/beevik/etree"
	"github.com/pkg/errors"
	"github.com/zeromake/zero-reader/pkg/parser/zip"
	"github.com/zeromake/zero-reader/pkg/typing"
	"io"
	"path"
	"strings"
	"time"
)

type Progress uint8

const (
	// progress
	PENDING Progress = iota
	ONLINE
	CONTENT
	METADATA
	MANIFEST
	SPINE
	COVER
	TOCS
	PAGES
	OFFLINE

	RootFileXPath = "//container/rootfiles/rootfile"
	MetaDataXPath = "//package/metadata"
	ManifestXPath = "//package/manifest"
	SpineXPath    = "//package/spine"
	CoverXPath    = "//package/guide/reference[@type='cover']"
	TocXPath      = "//ncx/navMap"

	TimeLayout = "2006-01-02T15:04:05+00:00"
)

var (
	PresumptiveContainerPaths = []string{
		"content.opf",
		"package.opf",
		"volume.opf",
		"OEBPS/content.opf",
		"OEBPS/package.opf",
		"OEBPS/volume.opf",
	}
	ContainerPaths = []string{
		"META-INF/container.xml",
		"container.xml",
	}
)

type Reader struct {
	r        *zip.Reader
	meta     *typing.Meta
	tocs     []*typing.Toc
	content  *typing.EpubContent
	manifest map[string]*typing.Manifest
	progress Progress
	spine    *typing.Spine
	cover    string
}

func NewReader(name string) (*Reader, error) {
	var (
		reader *zip.Reader
		err    error
	)
	if reader, err = zip.NewReader(name); err != nil {
		return nil, errors.WithStack(err)
	}
	return &Reader{
		r:        reader,
		progress: PENDING,
	}, nil
}

func (reader *Reader) Parse() error {
	err := reader.Progress(OFFLINE)
	return errors.WithStack(err)
}

func (reader *Reader) Join(elem string) string {
	return path.Join(reader.content.BasePath, elem)
}

func (reader *Reader) Find(id string) *typing.Manifest {
	return reader.manifest[id]
}

func SplitAnchor(url string) (string, string) {
	arr := strings.Split(url, "#")
	if len(arr) > 1 {
		return arr[0], arr[1]
	}
	return arr[0], ""
}

func (reader *Reader) Progress(end Progress) error {
	var (
		err error
	)
	start := reader.progress + 1
	for ; start <= end; start++ {
		switch start {
		case CONTENT:
			err = reader.parseContent()
		case METADATA:
			err = reader.parseMeta()
		case MANIFEST:
			err = reader.parseManifest()
		case SPINE:
			err = reader.parseSpine()
		case COVER:
			err = reader.parseCover()
		case TOCS:
			err = reader.parseToc()
		}
		if err != nil {
			return errors.WithStack(err)
		}
		reader.progress = start
	}
	return nil
}

func (reader *Reader) CheckProgress(start Progress) error {
	err := reader.Progress(start)
	if err != nil {
		return errors.WithStack(err)
	}
	return nil
}

func (reader *Reader) parseContent() error {
	var (
		file *gozip.File
		err  error
		read io.ReadCloser
	)
	for _, name := range ContainerPaths {
		if file, err = reader.r.Find(name); err == nil {
			d := etree.NewDocument()
			r, err := file.Open()
			if err != nil {
				return errors.WithStack(err)
			}
			_, err = d.ReadFrom(r)
			if err != nil {
				return errors.WithStack(err)
			}
			if err = r.Close(); err != nil {
				return errors.WithStack(err)
			}
			e := d.FindElement(RootFileXPath)
			file, err = reader.r.Find(e.SelectAttrValue("full-path", ""))
			if err != nil {
				break
			}
		}
	}
	if file == nil {
		for _, name := range PresumptiveContainerPaths {
			if file, err = reader.r.Find(name); err == nil {
				break
			}
		}
	}
	if read, err = file.Open(); err != nil {
		return errors.WithStack(err)
	}
	opfName := file.Name
	document := etree.NewDocument()

	if _, err = document.ReadFrom(read); err != nil {
		return errors.WithStack(err)
	}
	if err = read.Close(); err != nil {
		return errors.WithStack(err)
	}

	metaElement := document.FindElement(MetaDataXPath)
	manifestElement := document.FindElement(ManifestXPath)
	spine := document.FindElement(SpineXPath)
	cover := document.FindElement(CoverXPath)

	content := &typing.EpubContent{
		BasePath: path.Dir(opfName),
		Metadata: metaElement,
		Manifest: manifestElement,
		Spine:    spine,
		Cover:    cover,
	}
	reader.content = content
	return nil
}

func (reader *Reader) parseMeta() error {
	var (
		err error
	)
	element := reader.content.Metadata
	meta := &typing.Meta{
		BaseMeta: typing.BaseMeta{
			Author:   []string{},
			FileType: "epub",
		},
		Identifier: map[string]string{},
	}
	for _, child := range element.ChildElements() {
		switch child.Tag {
		case "title":
			meta.Title = child.Text()
		case "creator":
			meta.Author = append(meta.Author, child.Text())
		case "identifier":
			attr := child.SelectAttr("scheme")
			if attr != nil {
				meta.Identifier[strings.ToLower(attr.Value)] = child.Text()
			}
		case "date":
			meta.PubDate, err = time.Parse(TimeLayout, child.Text())
			if err != nil {
				return errors.WithStack(err)
			}
		case "publisher":
			meta.Publisher = child.Text()
		case "description":
			meta.Summary = child.Text()
		case "language":
			meta.Language = child.Text()
		}
	}
	reader.meta = meta
	return nil
}

func (reader *Reader) parseManifest() error {
	element := reader.content.Manifest
	if element == nil {
		return nil
	}
	manifestMap := map[string]*typing.Manifest{}
	for _, elem := range element.ChildElements() {
		manifest := &typing.Manifest{}
		for _, attr := range elem.Attr {
			switch attr.Key {
			case "href":
				manifest.Href = reader.Join(attr.Value)
			case "id":
				manifest.ID = attr.Value
			case "media-type":
				manifest.MediaType = attr.Value
			}
		}
		manifestMap[manifest.ID] = manifest
	}
	reader.manifest = manifestMap
	return nil
}

func (reader *Reader) parseSpine() error {
	element := reader.content.Spine
	if element == nil {
		return nil
	}
	spine := &typing.Spine{
		Toc:  element.SelectAttrValue("toc", ""),
		Refs: []string{},
	}
	for _, elem := range element.ChildElements() {
		attr := elem.SelectAttr("idref")
		if attr != nil {
			spine.Refs = append(spine.Refs, attr.Value)
		}
	}
	reader.spine = spine
	return nil
}

func (reader *Reader) parseCover() error {
	element := reader.content.Cover
	if element == nil {
		return nil
	}
	reader.cover = reader.Join(element.SelectAttrValue("href", ""))
	return nil
}
func (reader *Reader) deepToc(point *etree.Element, toc []*typing.Toc) ([]*typing.Toc, error) {
	var (
		text    *etree.Element
		content *etree.Element
		points  = []*etree.Element{}
		err     error
	)
	for _, child := range point.ChildElements() {
		switch child.Tag {
		case "navLabel":
			text = child.ChildElements()[0]
		case "content":
			content = child
		case "navPoint":
			points = append(points, child)
		}
	}
	src, anchor := SplitAnchor(content.SelectAttrValue("src", ""))
	if src != "" {
		src = reader.Join(src)
	}
	tocItem := &typing.Toc{
		Name:     text.Text(),
		ID:       point.SelectAttrValue("id", ""),
		Src:      src,
		Anchor:   anchor,
		Children: []*typing.Toc{},
	}
	toc = append(toc, tocItem)
	for _, p := range points {
		if tocItem.Children, err = reader.deepToc(p, tocItem.Children); err != nil {
			return nil, errors.WithStack(err)
		}
	}
	return toc, nil
}

func (reader *Reader) parseToc() error {
	manifest := reader.Find(reader.spine.Toc)
	tocFile, err := reader.r.Find(manifest.Href)
	if err != nil {
		return errors.WithStack(err)
	}
	file, err := tocFile.Open()
	if err != nil {
		return errors.WithStack(err)
	}
	document := etree.NewDocument()
	if _, err = document.ReadFrom(file); err != nil {
		return errors.WithStack(err)
	}
	tocElement := document.FindElement(TocXPath)
	if tocElement == nil {
		return nil
	}
	toc := []*typing.Toc{}
	for _, point := range tocElement.ChildElements() {
		if toc, err = reader.deepToc(point, toc); err != nil {
			return errors.WithStack(err)
		}
	}
	reader.tocs = toc
	return nil
}

func (reader *Reader) Content() (*typing.EpubContent, error) {
	err := reader.CheckProgress(CONTENT)
	if err != nil {
		return nil, errors.WithStack(err)
	}
	return reader.content, nil
}

func (reader *Reader) Meta() (*typing.Meta, error) {
	err := reader.CheckProgress(METADATA)
	if err != nil {
		return nil, errors.WithStack(err)
	}
	return reader.meta, nil
}

func (reader *Reader) Manifest() (map[string]*typing.Manifest, error) {
	err := reader.CheckProgress(MANIFEST)
	if err != nil {
		return nil, errors.WithStack(err)
	}
	return reader.manifest, nil
}

func (reader *Reader) Spine() (*typing.Spine, error) {
	err := reader.CheckProgress(SPINE)
	if err != nil {
		return nil, errors.WithStack(err)
	}
	return reader.spine, nil
}

func (reader *Reader) Cover() (string, error) {
	err := reader.CheckProgress(COVER)
	if err != nil {
		return "", errors.WithStack(err)
	}
	return reader.cover, nil
}

func (reader *Reader) Toc() ([]*typing.Toc, error) {
	err := reader.CheckProgress(TOCS)
	if err != nil {
		return nil, errors.WithStack(err)
	}
	return reader.tocs, nil
}

func (reader *Reader) Close() error {
	return errors.WithStack(reader.r.Close())
}
