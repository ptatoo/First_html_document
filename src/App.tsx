import ListGroup from "./components/ListGroup";
import Alert from "./components/Alert";
import SearchPanel from "./components/SearchPanel";

function App() {
  let items = ["New York", "San francisco", "Tokyo", "London", "Paris"];

  const handleSelectItem = (item: string) => {
    console.log(item);
  };

  return (
    <>
      <div>
        <SearchPanel />
      </div>
    </>
  );
}

export default App;
