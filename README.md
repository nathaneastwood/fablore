<a name="readme-top"></a>

# fablore

<a href="https://www.buymeacoffee.com/nathaneastwood"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a beer&emoji=🍺&slug=nathaneastwood&button_colour=ef60a3&font_colour=000000&font_family=Inter&outline_colour=000000&coffee_colour=FFDD00" /></a>

This repository contains the source of the [fablore](https://nathaneastwood.github.io/fablore/) book. This is a web book aiming to contain all known official Flesh and Blood lore. The book is built using [mdBook](https://github.com/rust-lang/mdBook).

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Building the Book

To build the book for yourself, make sure you have installed mdBook and then:

```
git clone https://github.com/nathaneastwood/fablore.git
cd fablore
mdbook build
```

To host your local version you can run

```
mdbook serve --open
```

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Images

When adding images to the book, be sure to convert them to [webp](https://chromium.googlesource.com/webm/libwebp) format using the `cwebp` tool.

```
for file in path/to/file/*; do cwebp -q 70 $file -o ${file%.*}.webp; done
```

Note, to install webp on your machine, please consult the [downloads page](https://developers.google.com/speed/webp/download) or [build instructions](https://chromium.googlesource.com/webm/libwebp/+/HEAD/doc/building.md).

## Extensions

This project makes use of the extensions and so you should:

* Copy the latest [index.hbs](https://github.com/rust-lang/mdBook/blob/master/src/theme/index.hbs) file

Such that you can:

* Include [mdbook-hints](https://github.com/caukub/mdbook-hints) with
    ```hbs
    <!-- Here -->
    <script src="https://unpkg.com/@popperjs/core@2"></script>
    <script src="https://unpkg.com/tippy.js@6"></script>

    <!-- Custom JS scripts -->
    ```
* Include [mdbook-pagetoc](https://github.com/slowsage/mdbook-pagetoc) by replacing
    ```hbs
    <main>
       {{{ content }}}
    </main>
    ```

    with:


    ```hbs
    <main><div class="sidetoc"><nav class="pagetoc"></nav></div>
        {{{ content }}}
    </main>
    ```

## License

All code in this repository is licensed under **_MIT_**, for more information take a look at the [LICENSE](https://github.com/nathaneastwood/fablore/blob/main/LICENSE) file. All content in the book is © Legend Story Studios.

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>
