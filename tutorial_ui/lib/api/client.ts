export class APIError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'APIError';
    }
}

type JsonValue = string | number | boolean | null | JsonObject | JsonArray;
type JsonObject = { [key: string]: JsonValue };
type JsonArray = JsonValue[];

class APIClient {
    private baseURL: string;

    constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    private async fetch(endpoint: string, options: RequestInit = {}): Promise<JsonValue | string> {
        const url = `${this.baseURL}${endpoint}`;

        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.text();
            throw new APIError(response.status, error);
        }

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return response.json() as Promise<JsonValue>;
        }
        return response.text();
    }

    async get(endpoint: string): Promise<JsonValue | string> {
        return this.fetch(endpoint, { method: 'GET' });
    }

    async post(endpoint: string, data: JsonValue): Promise<JsonValue | string> {
        return this.fetch(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async put(endpoint: string, data: JsonValue): Promise<JsonValue | string> {
        return this.fetch(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async delete(endpoint: string): Promise<JsonValue | string> {
        return this.fetch(endpoint, { method: 'DELETE' });
    }
}

export const apiClient = new APIClient();