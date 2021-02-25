import { nodeResolve } from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

import typescript from '@rollup/plugin-typescript';
import includePaths from 'rollup-plugin-includepaths';
 
const path = require('path');
const JS_ROOT = path.join(__dirname, '/npm_dist');

export default {
    input: 'es6/index.js',
    output: {
      file: 'es6/presto-parser-esm.js',
      format: 'es',
    },
    plugins: [
      nodeResolve({
        preferBuiltins: false,
      }),
      commonjs(),
      typescript({
        exclude: '*.js',
      }),
      includePaths({
        include: {},
        paths: [JS_ROOT],
        external: [],
        extensions: ['.js', '.ts']
      }),
    ],
  };