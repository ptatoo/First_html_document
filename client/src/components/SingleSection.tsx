interface Props {
  data: string[];
  sectionPara: string[];
}

function SingleSection({ data, sectionPara }: Props) {
  return <div>{data}</div>;
}

export default SingleSection;
