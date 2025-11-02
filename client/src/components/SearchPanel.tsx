import SearchType from "./SearchType";
import TermType from "./TermType";
import { useState } from "react";

interface Props {
  onGoSearch: (input: string, type: string) => void;
}

const SearchPanel = ({ onGoSearch }: Props) => {
  const retrieveGoSearch = (input: string, type: string) => {
    onGoSearch(input, type);
  };

  return (
    <>
      <TermType />
      <SearchType onSelectItem={retrieveGoSearch} />
    </>
  );
};

export default SearchPanel;
