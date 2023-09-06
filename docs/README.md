# Borgia documentation

This is the documentation folder of the Borgia project 

In order to use it inside this folder run the following commands to generate the documentation : 

- `make clean`
- `make html`

It will generate an html folder inside the _build directory. 

You will just have then to run the index.html inside a browser to see the Borgia documentation. 

---

If you want to host the documentation on a server or on GitHub : 

- https://python.plainenglish.io/how-to-host-your-sphinx-documentation-on-github-550254f325ae
- https://sphinx-intro-tutorial.readthedocs.io/en/latest/docs_hosting.html

---

The theme used is [The PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html)

---

A customization of this theme can be realize inside the `/_static/css/custom.css` file
- https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/styling.html

---

The extension `sphinx.ext.autodoc` is also installed in order to provide a complete API of the project.