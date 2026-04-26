import { useEffect, useRef } from 'react'

/**
 * Injects a Schema.org JSON-LD <script> tag into <head>.
 * Removes it on unmount so each route/tab gets a clean state.
 *
 * Usage:
 *   <JsonLd schema={buildFaqPageSchema()} id="faq-schema" />
 *
 * Props:
 *   schema  {object}  JSON-LD object (will be JSON.stringified)
 *   id      {string}  Unique DOM id — prevents duplicate injection (optional)
 */
export default function JsonLd({ schema, id }) {
  const elRef = useRef(null)

  useEffect(() => {
    // Remove any stale tag with the same id to avoid duplicates on hot-reload
    if (id) {
      const stale = document.getElementById(id)
      if (stale) stale.remove()
    }

    const script = document.createElement('script')
    script.type = 'application/ld+json'
    if (id) script.id = id
    script.textContent = JSON.stringify(schema)
    document.head.appendChild(script)
    elRef.current = script

    return () => {
      if (elRef.current && document.head.contains(elRef.current)) {
        document.head.removeChild(elRef.current)
      }
    }
  }, [schema, id])

  return null
}
