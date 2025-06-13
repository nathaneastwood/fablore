<a name="readme-top"></a>

# fablore

[![Build Status](https://github.com/nathaneastwood/fablore/actions/workflows/ci.yml/badge.svg)](https://github.com/nathaneastwood/fablore/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Flegendarystories.net)](https://legendarystories.net)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%E2%98%95-ef61a3.svg)](https://www.buymeacoffee.com/nathaneastwood)

**fablore** is the source repository for [Legendary Stories](https://legendarystories.net/), a community-curated digital archive of all known official *Flesh and Blood* lore. The site is built using [mdBook](https://github.com/rust-lang/mdBook).

## 🚀 Getting Started

### Prerequisites

* Install [mdBook](https://github.com/rust-lang/mdBook)
* Clone the repository:

```bash
git clone https://github.com/nathaneastwood/fablore.git
cd fablore
```

### Build the Book

```bash
mdbook build
```

### Serve Locally

```bash
mdbook serve --open
```

<p align="right"><a href="#readme-top">Back to top</a></p>

## 🖼️ Images

Images should be optimised and converted to [WebP](https://chromium.googlesource.com/webm/libwebp) format before use.

Convert a directory of images like so:

```bash
for file in path/to/files/*; do cwebp "$file" -o "${file%.*}.webp"; done
```

Install `cwebp` using your system package manager, or refer to the [official installation guide](https://developers.google.com/speed/webp/download).

<p align="right"><a href="#readme-top">Back to top</a></p>

## 🧩 Extensions

This project makes use of several mdBook extensions:

### `mdbook-hints`

Enable tooltips by adding the following to your `index.hbs`:

```html
<!-- Required by mdbook-hints -->
<script src="https://unpkg.com/@popperjs/core@2"></script>
<script src="https://unpkg.com/tippy.js@6"></script>
```

### `mdbook-pagetoc`

Enable per-page table of contents by modifying:

```hbs
<main>
   {{{ content }}}
</main>
```

to:

```hbs
<main>
  <div class="sidetoc">
    <nav class="pagetoc"></nav>
  </div>
  {{{ content }}}
</main>
```

Ensure you're using a custom theme and have copied the latest [`index.hbs`](https://github.com/rust-lang/mdBook/blob/master/src/theme/index.hbs) as a starting point.

<p align="right"><a href="#readme-top">Back to top</a></p>

## 🔍 Link Checking with `html-proofer`

To ensure all internal and external links in the built site are valid, run [`html-proofer`](https://github.com/gjtorikian/html-proofer):

```bash
gem install html-proofer
htmlproofer book/ --check-html --allow-hash-href
```

This will scan the `book/` output directory after building to catch broken links, missing anchors, and malformed HTML.

<p align="right"><a href="#readme-top">Back to top</a></p>

## 📏 Linking Rules

Heroes and documented places will have links to their respective pages. Characters, animals, plants, food, drink, etc. will have a hover over tooltip generated using [`mdbook-hints`](#mdbook-hints).

<p align="right"><a href="#readme-top">Back to top</a></p>

## 📜 License

Code in this repository is licensed under the **MIT License**. All lore content is © Legend Story Studios. See [LICENSE](./LICENSE) for details.

<p align="right"><a href="#readme-top">Back to top</a></p>
