# Amjad Saef

Quarto source for Amjad’s personal website. The rendered site in `docs/` can be opened directly in a browser. GitHub Pages can serve it from the main branch’s `/docs` directory.

## Editing

Edit `index.qmd`, `research.qmd`, `blog.qmd`, or `cv.qmd`. Run `quarto preview` at the repository root to review changes, then `quarto render` to update the complete site. Commit source and rendered files together.

Keep unpublished essays in `posts/_drafts/`. Drafts are visible in this public source repository and excluded from the rendered website. To publish one, move its `.qmd` file directly into `posts/`, render the site, and commit the changes. When unpublishing an essay, also remove its previously rendered file from `docs/posts/`. Until a post is published, Home and Blog display *Following soon!*

For a new essay, copy the existing essay to a new filename in the drafts folder. Set its title and a publication date (YYYY-MM-DD) in front matter. Leave the date out for an undated essay. Begin with two ordinary Markdown paragraphs. The first paragraph becomes the preview. The second is the destination of **Continue reading**. Home shows the newest essay; Blog shows all essays, ordered by descending date, with undated entries last. Markdown formatting, LaTeX and citations are supported; bibliographic records go in `references.bib`.

## Comments

The essay template includes a Disfora widget controlled by `disfora-enabled`. To enable it, register the site's domain with Disfora, configure Turnstile in its dashboard, enable guest comments, and select **Approve comments before they're public** for all readers. Set `disfora-enabled: true` in the essay front matter (or in `posts/_metadata.yml` for all essays), render, and check a guest submission followed by moderator approval. Turnstile secrets belong in the provider dashboard.

[Disfora installation](https://disfora.com/docs) · [Guest commenting and approval](https://admin.disfora.com/docs/guest-comments)
