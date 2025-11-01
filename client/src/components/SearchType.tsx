import { useState } from "react";
import GoButton from "./GoButton";

const SearchType = () => {
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

  function handleSearch() {
    console.log("Searching for: ", searchTerm);
    console.log("Search Type: ", selectedType);
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
      <button onClick={handleSearch}>Go</button>
    </>
  );
};

export default SearchType;
