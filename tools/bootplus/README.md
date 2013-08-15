# Based on [Bootplus v1.0.3](https://github.io/aozora/bootplus)

Bootplus is a front-end framework for faster and easier web development inspired by the lates Google+ look & feel, created and maintained by [Aozora](http://twitter.com/aozoralabs).

Bootplus is based on [Twitter Bootstrap](http://twitter.github.io/bootstrap)
To get started, check out [http://aozora.github.com/bootplus](http://aozora.github.io/bootplus)!

## Compiling CSS

Bootplus includes a [makefile](Makefile) with convenient methods for working with the framework. Before getting started, be sure to install [the necessary local dependencies](package.json):

```
$ npm install
```

When completed, you'll be able to run the various make commands provided:

#### build - `make`
Runs the recess compiler to rebuild the `/less` files and compiles the docs. Requires recess.

#### watch - `make watch`
This is a convenience method for watching just Less files and automatically building them whenever you save. Requires the Watchr gem.

Should you encounter problems with installing dependencies or running the makefile commands, be sure to first uninstall any previous versions (global and local) you may have installed, and then rerun `npm install`.


## Authors

**Marcello Palmitessa**

+ [http://twitter.com/aozoralabs](http://twitter.com/aozoralabs)
+ [https://github.com/aozora](https://github.com/aozora)


## Copyright and license

Bootplus is dual licensed, GPL-2 and Apache-2; see the LICENSE file.
