import { useState } from "react";
import GoButton from "./GoButton";

interface Props {
  onSelectItem: (item1: string, item2: string) => void;
}

const SearchType = ({ onSelectItem: onGoSearch }: Props) => {
  const search_type = [
    "Subject Area",
    "Class Units",
    "Class ID",
    "Instructor",
    "GE Classes",
    "Writing II Classes",
    "Diversity Classes",
    "College Honors Classes",
    "Fiat Lux Classes",
    "Community-Engaged Learning Classes",
    "USIE Seminars",
    "Law Classes",
    "Online - Classes Not Recorded",
    "Online - Classes Recorded",
    "Online - Asynchronous",
  ];
  const [selectedType, setSelectedIndex] = useState(search_type[0]);
  const [searchTerm, setSearchTerm] = useState("");

  function goSearch() {
    onGoSearch(searchTerm, selectedType);
  }

  return (
    <>
      <label>
        Search By:
        <select
          name="selectedSearch"
          onChange={(event) => {
            setSelectedIndex(event.target.value);
          }}
        >
          {search_type.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>

      <br></br>
      <label>
        Text input:{" "}
        <input
          type="text"
          placeholder={selectedType}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </label>
      <button onClick={goSearch}>Go</button>
    </>
  );
};

export default SearchType;
