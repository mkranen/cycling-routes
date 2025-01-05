import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../app/store";
import { setSport, Sport, sports } from "../routes/routeSlice";
import DistanceSlider from "../slider/DistanceSlider";

export default function Sidebar() {
    const sport = useSelector((state: RootState) => state.route.sport);
    const dispatch = useDispatch();

    return (
        <div className="w-full h-full p-4 bg-gradient-315 from-gray-800 to-gray-600 text-base-100">
            <div className="flex flex-col gap-4">
                <div className="form-control">
                    <label className="px-0 my-2">
                        <span className="text-base label-text text-base-100">Sport</span>
                    </label>
                    <select
                        className="w-full text-base-100 select select-bordered bg-slate-800"
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

                    <DistanceSlider />
                </div>
            </div>
        </div>
    );
}
