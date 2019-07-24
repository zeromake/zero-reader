package typing

import "github.com/beevik/etree"

type Manifest struct {
	File      string
	Href      string
	ID        string
	MediaType string
}

type Spine struct {
	Toc  string
	Refs []string
}

type EpubContent struct {
	BasePath string
	Manifest *etree.Element
	Spine    *etree.Element
	Cover    *etree.Element
	Metadata *etree.Element
}
