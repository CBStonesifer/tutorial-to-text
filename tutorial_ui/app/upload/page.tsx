"use client";

import { useState, useEffect, DragEvent, ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import { Timeline } from "@/components/timeline";

type UploadedFile = {
  file: File;
  id: string;
};

type FrameDescription = {
  timestamp: number;
  frame_number: number;
  description: string;
};

type ProcessResult = {
  video_url: string;
  filename: string;
  frames?: FrameDescription[];
  description?: string;
};

export default function UploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ProcessResult | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== "undefined") {
      const authenticated = sessionStorage.getItem("authenticated");
      if (!authenticated) {
        router.push("/");
      }
    }
  }, [router]);

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (fileList: FileList) => {
    const videoFiles = Array.from(fileList).filter((file) =>
      file.type.startsWith("video/")
    );

    const newFiles = videoFiles.map((file) => ({
      file,
      id: Math.random().toString(36).substring(7),
    }));

    setFiles(newFiles);
    setResult(null);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const loadTestData = async () => {
    setUploading(true);
    try {
      const response = await fetch("http://localhost:8000/api/test-timeline");
      if (response.ok) {
        const data = await response.json();
        setResult({
          video_url: data.video_url,
          filename: data.filename,
          frames: data.result?.frames,
          description: data.result?.description,
        });
      }
    } catch (error) {
      console.error("Error loading test data:", error);
    }
    setUploading(false);
    setFiles([]);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    const uploadedFile = files[0];
    const formData = new FormData();
    formData.append("file", uploadedFile.file);

    try {
      const response = await fetch("http://localhost:8000/api/upload-video", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResult({
          video_url: data.video_url,
          filename: data.filename,
          frames: data.result?.frames,
          description: data.result?.description,
        });
      } else {
        console.error(`Failed to upload ${uploadedFile.file.name}`);
      }
    } catch (error) {
      console.error(`Error uploading ${uploadedFile.file.name}:`, error);
    }

    setUploading(false);
    setFiles([]);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  const hasResults = result && (result.frames || result.description);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex justify-between items-center p-8 border-b bg-white">
        <h1 className="text-3xl font-bold text-gray-900">Tutorial Helper</h1>
        <div className="flex gap-4">
          <button
            onClick={loadTestData}
            className="hidden px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 border border-blue-600 rounded"
          >
            Load Test Data
          </button>
          <button
            onClick={() => {
              sessionStorage.removeItem("authenticated");
              router.push("/");
            }}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            Logout
          </button>
        </div>
      </div>

      <div className={hasResults ? "grid grid-cols-2 gap-8 p-8" : "p-8"}>
        <div className={hasResults ? "" : "max-w-4xl mx-auto w-full"}>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Upload Video
          </h2>

          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center ${
              dragActive
                ? "border-blue-500 bg-blue-50"
                : "border-gray-300 bg-white"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-upload"
              accept="video/*"
              onChange={handleChange}
              className="hidden"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center"
            >
              <svg
                className="w-16 h-16 text-gray-400 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="text-lg font-medium text-gray-700 mb-2">
                Drag and drop video here
              </p>
              <p className="text-sm text-gray-500">or click to browse</p>
            </label>
          </div>

          {files.length > 0 && (
            <div className="mt-8 bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">Selected File</h3>
              {files.map((uploadedFile) => (
                <div
                  key={uploadedFile.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-4"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      {uploadedFile.file.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(uploadedFile.file.size)}
                    </p>
                  </div>
                  <button
                    onClick={() => removeFile(uploadedFile.id)}
                    className="ml-4 text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              ))}

              <button
                onClick={handleUpload}
                disabled={uploading}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {uploading ? "Processing..." : "Upload & Process Video"}
              </button>
            </div>
          )}

          {result && result.video_url && (
            <div className="mt-8 bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">Video</h3>
              <a
                href={result.video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline"
              >
                View Uploaded Video
              </a>
            </div>
          )}
        </div>

        {hasResults && (
          <div className="bg-white rounded-lg shadow p-6 max-h-screen overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 sticky top-0 bg-white pb-4">
              Video Timeline
            </h2>
            {result.frames && result.frames.length > 0 ? (
              <Timeline items={result.frames} />
            ) : (
              <div className="bg-gray-50 rounded p-4">
                <p className="text-sm text-gray-700">{result.description}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
