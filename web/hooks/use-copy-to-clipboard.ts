import { useState } from 'react'

type CopiedValue = string | null
type CopyFn = (text: string) => Promise<boolean>

function useCopyToClipboard(): [CopiedValue, CopyFn] {
    const [copiedText, setCopiedText] = useState<CopiedValue>(null)

    const copy: CopyFn = async text => {
        if (!navigator?.clipboard) {
            console.warn('Clipboard not supported')
            // Use the 'out of viewport hidden text area' trick
            const textArea = document.createElement("textarea")
            textArea.value = text
                
            // Move textarea out of the viewport so it's not visible
            textArea.style.position = "absolute"
            textArea.style.left = "-999999px"
                
            document.body.prepend(textArea)
            textArea.select()

            try {
                document.execCommand('copy')
            } catch (error) {
                console.error(error)
            } finally {
                textArea.remove()
            }
            setCopiedText(text)
            return true
        }

        try {
            await navigator.clipboard.writeText(text)
            setCopiedText(text)
            return true
        } catch (error) {
            console.warn('Copy failed', error)
            setCopiedText(null)
            return false
        }
    }

    return [copiedText, copy]
}

export default useCopyToClipboard