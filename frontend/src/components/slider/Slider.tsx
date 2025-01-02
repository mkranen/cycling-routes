import * as RadixSlider from "@radix-ui/react-slider";
import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store";
import { setMaxDistance, setMinDistance } from "../routes/routeSlice";

export default function Slider({ onChange }: { onChange: (value: number[]) => void }) {
    const dispatch = useDispatch();
    const minDistance = useSelector((state: RootState) => state.route.minDistance);
    const maxDistance = useSelector((state: RootState) => state.route.maxDistance);
    const minRange = 0;
    const maxRange = 200;

    return (
        <form>
            <RadixSlider.Root
                className="relative flex items-center w-full h-5 select-none touch-none"
                defaultValue={[minDistance || 0, maxDistance || 100]}
                max={maxRange}
                min={minRange}
                step={1}
                onValueChange={([min, max]) => {
                    dispatch(setMinDistance(min));
                    dispatch(setMaxDistance(max));
                    onChange([min, max]);
                }}
            >
                <RadixSlider.Track className="relative w-full h-[3px] rounded-full bg-gray-200">
                    <RadixSlider.Range className="absolute h-full bg-blue-500 rounded-full" />
                </RadixSlider.Track>
                <RadixSlider.Thumb
                    className="block w-5 h-5 rounded-full shadow-md bg-base-100 hover:bg-gray-50 focus:outline-none"
                    aria-label="Min distance"
                />
                <RadixSlider.Thumb
                    className="block w-5 h-5 rounded-full shadow-md bg-base-100 hover:bg-gray-50 focus:outline-none"
                    aria-label="Max distance"
                />
            </RadixSlider.Root>
            <div className="flex justify-between mt-2 text-sm">
                <span>{minDistance || 0}km</span>
                <span>{maxDistance || 100}km</span>
            </div>
        </form>
    );
}
