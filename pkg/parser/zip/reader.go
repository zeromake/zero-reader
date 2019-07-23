package zip

import (
	"archive/zip"
	"github.com/pkg/errors"
	"io"
	"os"
	"path"
	"strings"
)

const (
	UMARK = 022
	DIR_MARK = 777 - UMARK
	FILE_MAEK = 666 - UMARK
	FILE_FLAG = os.O_CREATE|os.O_WRONLY|os.O_TRUNC
)

type Reader struct {
	r *zip.ReadCloser
}

func NewReader(name string) (*Reader, error) {
	r, err := zip.OpenReader(name)
	if err != nil {
		return nil, errors.WithStack(err)
	}
	read := &Reader{
		r,
	}
	return read, nil
}

func Join(elem ...string) string {
	for i, e := range elem {
		if e != "" {
			return path.Clean(strings.Join(elem[i:], "/"))
		}
	}
	return ""
}

func (r *Reader) Find(name string) (*zip.File, error) {
	for _, f := range r.r.File {
		if strings.EqualFold(f.Name, name) {
			return f, nil
		}
	}
	return nil, errors.WithStack(os.ErrNotExist)
}

// Open open zip file
func (r *Reader) Open(name string) (io.ReadCloser, error) {
	file, err := r.Find(name)
	if err != nil  {
		return nil, errors.WithStack(err)
	}
	f, err := file.Open()
	return f, errors.WithStack(err)
}

func (r *Reader) Close() error {
	return errors.WithStack(r.r.Close())
}

func (r *Reader) Save(target string, source string) (int64, error) {
	dst, err := os.OpenFile(target, FILE_FLAG, FILE_MAEK)
	if err != nil {
		return 0, errors.WithStack(err)
	}
	return r.SaveWriter(dst, source)
}

func (r *Reader) SaveWriter(target io.Writer, source string) (int64, error) {
	src, err := r.Open(source)
	if err != nil {
		return 0, errors.WithStack(err)
	}
	count, err := io.Copy(target, src)
	if err = src.Close(); err != nil {
		return 0, errors.WithStack(err)
	}
	return count, errors.WithStack(err)
}

func (r *Reader) Range(f func(file *zip.File) bool) {
	for _, file := range r.r.File {
		if !f(file) {
			break
		}
	}
}

func (r *Reader) Extract(target string) error {
	var (
		src io.ReadCloser
		dst io.WriteCloser
		err error
		file *zip.File
	)
	for _, file = range r.r.File {
		if file.FileInfo().IsDir() {
			// 文件夹处理
			err = os.Mkdir(path.Join(target, file.Name), file.Mode())
			if err != nil {
				return errors.WithStack(err)
			}
			continue
		}
		dst, err = os.OpenFile(path.Join(target, file.Name), FILE_FLAG, file.Mode())
		if err != nil {
			return errors.WithStack(err)
		}
		if src, err = file.Open(); err != nil {
			return errors.WithStack(err)
		}
		if _, err = io.Copy(dst, src); err != nil {
			return errors.WithStack(err)
		}
		if err = src.Close(); err != nil {
			return errors.WithStack(err)
		}
		if err = dst.Close(); err != nil {
			return errors.WithStack(err)
		}
	}
	return nil
}

func (r *Reader) RegisterDecompressor(method uint16, dcomp zip.Decompressor) {
	r.r.RegisterDecompressor(method, dcomp)
}
