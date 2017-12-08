var defaultConfig = {
  rootMargin: '0px',
  threshold: 0,
  target: document,
  load(element) {
    if (element.getAttribute('data-src')) {
      element.src = element.getAttribute('data-src')
    }
    if (element.getAttribute('data-srcset')) {
      element.srcset = element.getAttribute('data-srcset')
    }
    if (element.getAttribute('data-background-image')) {
      element.style.backgroundImage = 'url(' + element.getAttribute('data-background-image') + ')'
    }
  }
}

function markAsLoaded(element) {
  element.setAttribute('data-loaded', true)
}

var isLoaded = element => element.getAttribute('data-loaded') === 'true'

var onIntersection = load => (entries, observer) => {
  entries.forEach(entry => {
    if (entry.intersectionRatio > 0) {
      observer.unobserve(entry.target)

      if (!isLoaded(entry.target)) {
        load(entry.target)
        markAsLoaded(entry.target)
      }
    }
  })
}

export default function (selector = '.lozad', options = {}) {
  var options = Object.assign({}, defaultConfig, options)
  var {rootMargin, threshold, load, target} = {...defaultConfig, ...options}
  var observer

  if (window.IntersectionObserver) {
    observer = new IntersectionObserver(onIntersection(load), {
      rootMargin,
      threshold
    })
  }

  var elements = target.querySelectorAll(selector)
  return {
    observe() {
      for (let i = 0; i < elements.length; i++) {
        if (isLoaded(elements[i])) {
          continue
        }
        if (observer) {
          observer.observe(elements[i])
          continue
        }
        load(elements[i])
        markAsLoaded(elements[i])
      }
    },
    triggerLoad(element) {
      if (isLoaded(element)) {
        return
      }

      load(element)
      markAsLoaded(element)
    },
    unobserve() {
      for (let i = 0; i < elements.length; i++) {
          observer.unobserve(elements[i])
      }
    }
  }
}