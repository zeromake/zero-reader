package epub

// Toc epub toc
type Toc struct {
	Name  string
	Src   string
	Level uint
	Anchor  string
	Children []Toc
}

type MateData struct {

}

type OpfData struct {

}
