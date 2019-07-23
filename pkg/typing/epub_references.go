package typing

type Manifest struct {
	Href string
	ID string
	MediaType string
}

type EpubContent struct {
	BasePath string
	Manifest map[string]*Manifest
	Spine []string
	Cover string
	Metadata *Meta
}
