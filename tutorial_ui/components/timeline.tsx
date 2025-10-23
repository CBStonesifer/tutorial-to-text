"use client";

import {Check} from "lucide-react";
import {cn} from "@/lib/utils";

type TimelineItem = {
    timestamp: number;
    description: string;
    frame_number: number;
};

type TimelineProps = {
    items: TimelineItem[];
    className?: string;
};

export function Timeline({items, className}: TimelineProps) {
    const formatTimestamp = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    const extractAssistantResponse = (description: string): string => {
        const assistantIndex = description.indexOf("Assistant: ");
        if (assistantIndex === -1) {
            return "---Videoframe indistinguishable---";
        }
        return description.substring(assistantIndex + "Assistant: ".length);
    };

    return (
        <div className={cn("relative space-y-8", className)}>
            {items.map((item, index) => (
                <div key={item.frame_number} className="relative flex gap-4">
                    <div className="flex flex-col items-center">
                        <div
                            className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-blue-600 bg-white">
                            <Check className="h-5 w-5 text-blue-600"/>
                        </div>
                        {index < items.length - 1 && (
                            <div className="h-full w-0.5 bg-blue-200"/>
                        )}
                    </div>

                    <div className="flex-1 pb-8">
                        <div className="flex items-baseline gap-2 mb-1">
              <span className="text-sm font-semibold text-blue-600">
                {formatTimestamp(item.timestamp)}
              </span>
                            <span className="text-xs text-gray-500">
                Frame {item.frame_number}
              </span>
                        </div>
                        <p className="text-sm text-gray-700 leading-relaxed">
                            {extractAssistantResponse(item.description)}
                        </p>
                    </div>
                </div>
            ))}
        </div>
    );
}
