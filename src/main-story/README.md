# Main Story

This folder contains the files for the main storyline in the world of Rathe. Below you can find instructions for adding a newly released story to the Legendary Stories site.

To aid this instruction set, we will use the Squeaker's Christmas story, which was written as part of the Outsider's release, as an example.

* Copy the content into a markdown file under the `10-outsiders` folder. The name should be written in `hyphen-case-name`, i.e. `squeakers-christmas.md`.
* Save any images for the story to the `10-outsiders/media`. Images should be converted to `.webp` format. File names should have the story's name followed by a number which follows the order they appear in the story, i.e. `squeakers-christmas-1.webp`.
* At the bottom of the file, add any source(s) for the story (e.g. the fabtcg.com link) as well as any information about the writer(s), director(s) and illustrator(s) in italics.
* If available, add the narrated YouTube video to the very bottom of the file.
* Replace any non-standard ligatures such as `“`, `”`, `’`, `—`, `…` with the standard ones `"`, `"`, `'`, `-` and `...`.
* Replace any horizontal bars with `---` which creates a horizontal bar using markdown.
* Add links to the first mention of each unique hero, character or location.
* Add any mentions of new characters, heroes or locations to the [data files](../data).
* Add the story to the [SUMMARY.md](../SUMMARY.md) file. 

The final file should have the following format:

```
# Title

<p>
(<a href="#narrated-video">Jump to Narrated Video</a>)
</p>

Content

---

_Source: [https://fabtcg.com/articles/...](https://fabtcg.com/articles/...)_<br>
_Stories written by ..._<br>
_Directed by ... Illus. by ..._

---

## Narrated Video

<p>
(<a href="#title">Jump to the Top</a>)
</p>

<div style="text-align: center;"><iframe ...</iframe></div>
```
