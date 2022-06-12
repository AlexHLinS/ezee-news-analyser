import React, {FC} from 'react';


const Header: FC = () => {
	return (
		<header className="pt-3">
			<nav className="navbar navbar-expand-lg navbar-light">
				<div className="container">
					<a className="navbar-brand" href="src/components/Header#/">
						<img src={ require("../img/logo.png")} height="65" className="" alt=""/>
					</a>
					<div className="d-flex justify-content-end">
						<a className="nav-link" href="src/components/Header#/">
							<img src={ require("../img/telegram.png")} height="26" className="" alt="" />
								&nbsp;@Telegram-bot
						</a>
					</div>
				</div>
			</nav>
		</header>
	);
};

export default Header;