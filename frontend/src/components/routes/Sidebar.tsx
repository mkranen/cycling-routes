import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store";
import { setSport, Sport, sports } from "./routeSlice";

export default function Sidebar() {
    const sport = useSelector((state: RootState) => state.route.sport);
    const dispatch = useDispatch();
    return (
        <div className="w-full h-full p-4">
            <div className="text-2xl">Routes</div>

            <div className="form-control">
                <select
                    className="w-full max-w-xs select select-bordered"
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
            {/* <div className="form-control">
                <label className="cursor-pointer label">
                    <span className="label-text">Remember me</span>
                    <input type="checkbox" checked={true} className="checkbox checkbox-accent" />
                </label>
            </div> */}
        </div>
    );
}
