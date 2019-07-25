package epub

import (
	"fmt"
	"testing"
)

const (
	fileName = "/Users/macbook/Documents/project/library/css/CSS揭秘.epub"
)

func TestReader_ParseReferences(t *testing.T) {
	reader, err := NewReader(fileName)
	if err != nil {
		fmt.Printf("%+v\n", err)
		return
	}
	err = reader.Parse()
	if err != nil {
		fmt.Printf("%+v\n", err)
		return
	}
	defer reader.Close()
	writer := &DefaultWriter{
		Out: "./out",
	}
	err = reader.WriteAll(writer)
	if err != nil {
		fmt.Printf("%+v\n", err)
		return
	}
}
