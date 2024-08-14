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

import { render, screen, waitFor, act } from '@testing-library/react';
import React from 'react';
import useFetch from './useFetch';
import { get } from '../../api/utils';

// Mock the `get` function
jest.mock('../../api/utils', () => ({
    get: jest.fn(),
}));

const mockGet = get as jest.MockedFunction<typeof get>;
const mockUrlPrefix = 'https://api.example.com';
const mockEndpoint = '/endpoint';
const mockUrl = `${mockUrlPrefix}${mockEndpoint}`;

// Create a test component that uses the hook
const TestComponent: React.FC<{ url?: string, options?: any }> = ({ url, options }) => {
    const { data, loading, error, refetch } = useFetch(url, options);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    if (data) return (
        <>
            <div>Data: {JSON.stringify(data)}</div>
            <button onClick={refetch}>Refetch</button>
        </>
    );

    return null;
};

describe('useFetch', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('should fetch data successfully', async () => {
        const mockData = { id: 1, product: 'Hue' };
        mockGet.mockResolvedValue(mockData);

        render(<TestComponent url={mockEndpoint} />);

        expect(screen.getByText('Loading...')).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByText(`Data: ${JSON.stringify(mockData)}`)).toBeInTheDocument();
        });
    });

    it('should fetch data with params successfully', async () => {
        const mockData = { id: 1, product: 'Hue' };
        mockGet.mockResolvedValue(mockData);

        const mockParams = { id: 1 };

        render(<TestComponent url={mockEndpoint} options={{
            urlPrefix: mockUrlPrefix,
            params: mockParams,
        }} />);

        expect(screen.getByText('Loading...')).toBeInTheDocument();

        await waitFor(() => {
            expect(mockGet).toHaveBeenCalledWith(mockUrl, mockParams, expect.any(Object));
            expect(screen.getByText(`Data: ${JSON.stringify(mockData)}`)).toBeInTheDocument();
        });
    });

    it('should handle fetch errors', async () => {
        const mockError = new Error('Fetch error');
        mockGet.mockRejectedValue(mockError);

        render(<TestComponent url={mockEndpoint} />);

        expect(screen.getByText('Loading...')).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByText(`Error: ${mockError.message}`)).toBeInTheDocument();
        });
    });

    it('should respect the skip option', () => {
        render(<TestComponent url={mockEndpoint} options={{ skip: true }} />);

        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
        expect(screen.queryByText(/Error:/)).not.toBeInTheDocument();
        expect(screen.queryByText(/Data:/)).not.toBeInTheDocument();
    });

    it('should call refetch function', async () => {
        const mockData = { id: 1, product: 'Hue' };
        mockGet.mockResolvedValueOnce(mockData).mockResolvedValueOnce(mockData);

        render(<TestComponent url={mockEndpoint} />);

        await waitFor(() => {
            expect(screen.getByText(`Data: ${JSON.stringify(mockData)}`)).toBeInTheDocument();
        });

        act(() => {
            screen.getByText('Refetch').click();
        });

        await waitFor(() => {
            expect(screen.getByText(`Data: ${JSON.stringify(mockData)}`)).toBeInTheDocument();
        });
    });

    it('should handle URL prefix correctly', async () => {
        const mockData = { id: 1, product: 'Hue' };
        mockGet.mockResolvedValue(mockData);

        render(<TestComponent url={mockEndpoint} options={{ urlPrefix: mockUrlPrefix }} />);

        await waitFor(() => {
            expect(mockGet).toHaveBeenCalledWith(mockUrl, undefined, expect.any(Object));
            expect(screen.getByText(`Data: ${JSON.stringify(mockData)}`)).toBeInTheDocument();
        });
    });

    it('should update options correctly', async () => {
        const mockData = { id: 1, product: 'Hue' };
        mockGet.mockResolvedValue(mockData);

        const { rerender } = render(
            <TestComponent url={mockEndpoint} options={{ urlPrefix: mockUrlPrefix }} />
        );

        await waitFor(() => {
            expect(screen.getByText(`Data: ${JSON.stringify(mockData)}`)).toBeInTheDocument();
        });

        rerender(<TestComponent url={mockEndpoint} options={{ urlPrefix: 'https://api.example.com/v2' }} />);

        await waitFor(() => {
            expect(mockGet).toHaveBeenCalledWith('https://api.example.com/v2/endpoint', undefined, expect.any(Object));
        });
    });
});
