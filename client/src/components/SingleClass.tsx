import SingleSection from "./SingleSection";

interface Props {
  singleClassData: string[][];
  key: string;
}

function SingleClass({ singleClassData }: Props) {
  return (
    <>
      <div className="single class">
        {singleClassData.map((item) => (
          <SingleSection data={item} sectionPara={[]} />
        ))}
      </div>
    </>
  );
}

export default SingleClass;
