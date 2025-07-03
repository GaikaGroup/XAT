// jest.setup.ts
Object.defineProperty(window.HTMLElement.prototype, 'scrollIntoView', {
  configurable: true,
  value: () => {},
});

// Add TextEncoder and TextDecoder polyfills
class TextEncoderPolyfill {
  encode(input: string): Uint8Array {
    const utf8 = unescape(encodeURIComponent(input));
    const result = new Uint8Array(utf8.length);
    for (let i = 0; i < utf8.length; i++) {
      result[i] = utf8.charCodeAt(i);
    }
    return result;
  }
}

class TextDecoderPolyfill {
  decode(input?: Uint8Array): string {
    if (!input) return '';
    return decodeURIComponent(escape(String.fromCharCode.apply(null, Array.from(input))));
  }
}

global.TextEncoder = TextEncoderPolyfill as any;
global.TextDecoder = TextDecoderPolyfill as any;
