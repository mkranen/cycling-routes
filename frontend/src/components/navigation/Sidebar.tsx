import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../app/store";
import { collections, setSelectedCollections, setSport, sports } from "../routes/routeSlice";
import DistanceSlider from "../slider/DistanceSlider";
import ReactSelect from "./ReactSelect";

export default function Sidebar() {
    const selectedSport = useSelector((state: RootState) => state.route.sport);
    const selectedCollections = useSelector((state: RootState) => state.route.selectedCollections);
    const dispatch = useDispatch();

    return (
        <div className="w-full h-full p-4 bg-gradient-315 from-gray-800 to-gray-600 text-base-100">
            <div className="flex flex-col gap-4">
                <ReactSelect
                    options={sports}
                    value={selectedSport}
                    placeholder="All"
                    onChange={(options: any) => dispatch(setSport(options))}
                />

                <ReactSelect
                    options={collections}
                    value={selectedCollections}
                    placeholder="All"
                    isMulti
                    onChange={(options: any) => dispatch(setSelectedCollections(options))}
                />

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
