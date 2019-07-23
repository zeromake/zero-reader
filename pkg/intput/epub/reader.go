package epub

import (
	gozip "archive/zip"
	"github.com/beevik/etree"
	"github.com/pkg/errors"
	"github.com/zeromake/zero-reader/pkg/parser/zip"
	"github.com/zeromake/zero-reader/pkg/typing"
	"io"
	"strings"
	"time"
)

const (
	RootFileXPath = "//container/rootfiles/rootfile"
	MetaDataXPath = "//package/metadata"
	ManifestXPath = "//package/manifest"
	TocXPath = "//package/spine"
	CoverXPath = "//package/guide/reference[@type='cover']"

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
	r *zip.Reader
	meta *typing.BaseMeta
	tocs []typing.Toc
}

func NewReader(name string) (*Reader, error) {
	var (
		reader *zip.Reader
		err error
	)
	if reader, err = zip.NewReader(name); err != nil {
		return nil, errors.WithStack(err)
	}
	return &Reader{
		r: reader,
	}, nil
}

func (reader *Reader)Parse() error {

	return nil
}

func (reader *Reader) ParseReferences() (*typing.EpubContent, error) {
	var (
		file *gozip.File
		err error
		read io.ReadCloser
	)
	for _, name := range ContainerPaths {
		if file, err = reader.r.Find(name); err == nil {
			d := etree.NewDocument()
			r, err := file.Open()
			if err != nil {
				return nil, errors.WithStack(err)
			}
			_, err = d.ReadFrom(r)
			if err != nil {
				return nil, errors.WithStack(err)
			}
			if err = r.Close(); err != nil {
				return nil, errors.WithStack(err)
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
		return nil, errors.WithStack(err)
	}
	document := etree.NewDocument()

	if _, err = document.ReadFrom(read); err != nil {
		return nil, errors.WithStack(err)
	}
	if err = read.Close(); err != nil {
		return nil, errors.WithStack(err)
	}

	metaElement := document.FindElement(MetaDataXPath)
	content := &typing.EpubContent{
		Manifest: map[string]*typing.Manifest{},
	}
	if metaElement != nil {
		meta, err := reader.ParseMeta(metaElement)
		if err != nil {
			return nil, errors.WithStack(err)
		}
		content.Metadata = meta
	}
	manifestElement := document.FindElement(ManifestXPath)
	if manifestElement != nil {
		for _, elem := range manifestElement.ChildElements() {
			manifest := &typing.Manifest{}
			for _, attr := range elem.Attr {
				switch attr.Key {
				case "href":
					manifest.Href = attr.Value
				case "id":
					manifest.ID = attr.Value
				case "media-type":
					manifest.MediaType = attr.Value
				}
			}
			content.Manifest[manifest.ID] = manifest
		}
	}


	return nil, nil
}

func (reader *Reader) ParseMeta(element *etree.Element) (*typing.Meta, error) {
	var (
		err error
	)
	meta := &typing.Meta{
		BaseMeta: typing.BaseMeta{
			Author: []string{},
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
				return nil, errors.WithStack(err)
			}
		case "publisher":
			meta.Publisher = child.Text()
		case "description":
			meta.Summary = child.Text()
		case "language":
			meta.Language = child.Text()
			
		}
	}
	return meta, nil
}

func (reader *Reader) Close() error {
	return errors.WithStack(reader.r.Close())
}
