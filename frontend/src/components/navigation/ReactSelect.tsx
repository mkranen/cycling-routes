import { ClearIndicatorProps, DropdownIndicatorProps, MultiValueRemoveProps, Props } from "react-select";

import { components } from "react-select";

import clsx from "clsx";
import React from "react";
import { FaChevronDown, FaTimes } from "react-icons/fa";
import Select from "react-select";

const DropdownIndicator = (props: DropdownIndicatorProps) => {
    return (
        <components.DropdownIndicator {...props}>
            <FaChevronDown />
        </components.DropdownIndicator>
    );
};

const ClearIndicator = (props: ClearIndicatorProps) => {
    return (
        <components.ClearIndicator {...props}>
            <FaTimes />
        </components.ClearIndicator>
    );
};

const MultiValueRemove = (props: MultiValueRemoveProps) => {
    return (
        <components.MultiValueRemove {...props}>
            <FaTimes />
        </components.MultiValueRemove>
    );
};

const textStyles = "text-base-100";
const bgStyles = "bg-slate-800";
const bgHoverStyles = "hover:bg-slate-900";
const bgSelectStyles = "bg-slate-950";
const borderStyles = "border-gray-200";

const controlStyles = {
    base: `${textStyles} ${bgStyles} w-full text-base-100 select hover:cursor-pointer px-1`,
    focus: "",
    nonFocus: "",
};
const placeholderStyles = `${textStyles} pl-1 py-0.5`;
const selectInputStyles = `${textStyles} pl-1 py-0.5`;
const valueContainerStyles = "p-1 gap-1";
const singleValueStyles = "leading-7 ml-1";
const multiValueStyles = `${bgSelectStyles} rounded items-center py-0.5 pl-2 pr-1 gap-1.5`;
const multiValueLabelStyles = "leading-6 py-0.5";
const multiValueRemoveStyles = `${bgStyles} ${borderStyles} hover:bg-red-50 hover:text-red-800 text-gray-500 hover:border-red-300 rounded-md`;
const indicatorsContainerStyles = "p-1 gap-1";
const clearIndicatorStyles = `${textStyles} p-1 rounded-md hover:bg-red-50 hover:text-red-800`;
const dropdownIndicatorStyles = `${textStyles} p-1 hover:bg-gray-100 rounded-md hover:text-black`;
const menuStyles = `${textStyles} ${bgStyles} ${borderStyles} p-1 mt-2  rounded-lg`;
const groupHeadingStyles = `${textStyles} ml-3 mt-2 mb-1 text-sm`;
const optionStyles = {
    base: "hover:cursor-pointer px-3 py-2 rounded",
    focus: `${textStyles} ${bgHoverStyles}`,
    selected: `${textStyles} ${bgSelectStyles}`,
};
const noOptionsMessageStyles = `${textStyles} ${borderStyles} p-2 bg-gray-50 border border-dashed rounded-sm`;

export default function ReactSelect({ value, options, onChange, placeholder, isMulti = false, ...props }: Props) {
    return (
        <Select
            value={value}
            options={options}
            isMulti={isMulti}
            unstyled
            isClearable={false}
            placeholder={placeholder}
            styles={{
                input: (base) => ({
                    ...base,
                    "input:focus": {
                        boxShadow: "none",
                    },
                }),
                // On mobile, the label will truncate automatically, so we want to
                // override that behaviour.
                multiValueLabel: (base) => ({
                    ...base,
                    whiteSpace: "normal",
                    overflow: "visible",
                }),
                control: (base) => ({
                    ...base,
                    transition: "none",
                }),
            }}
            onChange={onChange}
            components={{ DropdownIndicator, ClearIndicator, MultiValueRemove }}
            classNames={{
                control: ({ isFocused }) =>
                    clsx(isFocused ? controlStyles.focus : controlStyles.nonFocus, controlStyles.base),
                placeholder: () => placeholderStyles,
                input: () => selectInputStyles,
                valueContainer: () => valueContainerStyles,
                singleValue: () => singleValueStyles,
                multiValue: () => multiValueStyles,
                multiValueLabel: () => multiValueLabelStyles,
                multiValueRemove: () => multiValueRemoveStyles,
                indicatorsContainer: () => indicatorsContainerStyles,
                clearIndicator: () => clearIndicatorStyles,
                dropdownIndicator: () => dropdownIndicatorStyles,
                menu: () => menuStyles,
                groupHeading: () => groupHeadingStyles,
                option: ({ isFocused, isSelected }) =>
                    clsx(isFocused && optionStyles.focus, isSelected && optionStyles.selected, optionStyles.base),
                noOptionsMessage: () => noOptionsMessageStyles,
            }}
            {...props}
        />
    );
}
