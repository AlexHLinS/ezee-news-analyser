import React, {FC} from 'react';


const RightBlock: FC = () => {
	return (
		<div className="col-12 col-lg-5">
			<img className="img-fluid mx-auto d-block"
                 src={ require("../img/danila_truth.png")} alt=""/>
		</div>
	);
};

export default RightBlock;