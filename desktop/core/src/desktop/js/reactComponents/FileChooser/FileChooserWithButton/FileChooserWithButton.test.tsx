// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import React from 'react';

import FileChooserWithButton from './FileChooserWithButton';

test('Filechooser modal opens on button click', async () => {
  const user = userEvent.setup();
  const { queryByText } = render(<FileChooserWithButton title={'File chooser component'} />);
  await user.click(screen.getByRole('button', { name: 'File chooser component' }));
  expect(queryByText('Choose a file')).toBeInTheDocument();
});
