import SearchPanel from "./components/SearchPanel";
import Classes from "./components/Classes";
import { useState } from "react";

function App() {
  const [input, setInput] = useState("");
  const [type, setType] = useState("");
  const [sectionData, setSectionData] = useState([]);
  const sectionPara = [
    "classId",
    "lec_dis",
    "total_spots",
    "enrollled_spots",
    "waitlist_status",
    "days",
    "start_time",
    "end_time",
    "location",
    "units",
    "instructors",
  ];

  const retrieveGoSearch = (input: string, type: string) => {
    setInput(input);
    setType(type);
    console.log("Apps retrieved input and search type");
    retrieveClassData();
  };

  //fetches data and stores it as 2D array
  async function retrieveClassData() {
    //fetch data from server
    try {
      const response = await fetch("http://localhost:3000/");
      if (!response.ok) {
        throw new Error("HTTP error: ${response.status}");
      }
      const jsonData = await response.json();

      //convert data from object to 2D array
      const allSections = jsonData.map((item: any) => {
        return sectionPara.map((key) => item[key]);
      });
      setSectionData(allSections);
    } catch (error) {
      console.error("Error message: ", error);
    }
  }

  return (
    <>
      <div>
        <SearchPanel onGoSearch={retrieveGoSearch} />
      </div>
      <Classes data={sectionData} sectionPara={sectionPara} />
    </>
  );
}

export default App;
