import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store";
import Slider from "../slider/Slider";
import { setSport, Sport, sports } from "./routeSlice";

export default function Sidebar() {
    const sport = useSelector((state: RootState) => state.route.sport);
    const [distance, setDistance] = useState<number[]>([20, 80]);
    const dispatch = useDispatch();

    return (
        <div className="w-full h-full p-4 bg-gradient-to-r from-gray-700 to-gray-600 text-base-100">
            <div className="text-2xl">Routes</div>

            <div className="flex flex-col gap-4">
                <div className="form-control">
                    <label className="px-0 my-2">
                        <span className="text-base label-text text-base-100">Sport</span>
                    </label>
                    <select
                        className="w-full max-w-xs text-base-content select select-bordered"
                        onChange={(e) => dispatch(setSport(e.target.value as Sport))}
                        value={sport || ""}
                    >
                        {Object.keys(sports).map((id) => (
                            <option key={id} value={id}>
                                {sports[id]}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="form-control">
                    <label className="px-0 my-2">
                        <span className="text-base label-text text-base-100">Distance</span>
                    </label>

                    <Slider
                        onChange={([min, max]) => {
                            setDistance([min, max]);
                        }}
                    />
                </div>
            </div>

            {/* <div className="form-control">
                <label className="cursor-pointer label">
                    <span className="label-text">Remember me</span>
                    <input type="checkbox" checked={true} className="checkbox checkbox-accent" />
                </label>
            </div> */}
        </div>
    );
}
