import React, {FC, useEffect, useState} from 'react';
import RightBlock from './RightBlock';
// @ts-ignore
import isUrl from 'validator/es/lib/isURL';
import NewsService from "../API/NewsService";

export interface newsData {
    url?: string;
    text?: string;
}

const Form: FC = () => {
	const [newsUrl, setNewsURl] = useState<string>('')
	const [newsText, setNewsText] = useState<string>('')

	const [newsUrlDisabled, setNewsUrlDisabled] = useState<boolean>(false)
	const [newsTextDisabled, setNewsTextDisabled] = useState<boolean>(false)
	const [buttonDisabled, setButtonDisabled] = useState<boolean>(true)

	const [isUrlCorrect, setIsUrlCorrect] = useState<boolean>(true)

	const [isLoading, setIsLoading] = useState<boolean>(false)

	const focusUrlHandler = (e: React.ChangeEvent<HTMLInputElement>) => {
			setNewsTextDisabled(true);
			setNewsText('')
	}
	const blurUrlHandler = (e: React.ChangeEvent<HTMLInputElement>) => {
			setNewsTextDisabled(false);
	}
	const focusTextHandler = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
			setIsUrlCorrect(true);
			setNewsURl('')
			setNewsUrlDisabled(true);
	}
	const blurTextHandler = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
			setNewsUrlDisabled(false);
	}


	const changeUrlHandler = (e: React.ChangeEvent<HTMLInputElement>) => {
		if (!e.target.value) {
			setIsUrlCorrect(true)
		}
		setNewsURl(e.target.value);
	}
	const changeTextHandler = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		setButtonDisabled(false);
		setNewsText(e.target.value);
	}

	async function postForm(news: newsData) {
		const response = await NewsService.postNews(news)
		console.log(response)
	}


	const submitForm = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault()
		if (newsUrl && !isUrl(newsUrl)) {
			setIsUrlCorrect(false)
		} else if (newsUrl) {
			setIsUrlCorrect(true)
			postForm({url: newsUrl})
		} else {
			setIsUrlCorrect(true)
		}
		if (newsText) {
			postForm({text: newsText})
		}
	}

	useEffect(() => {
    if (newsUrl || newsText)  {
			setButtonDisabled(false)
		} else {
			setButtonDisabled(true)
		}
  }, [newsUrl, newsText])


	return (
		<section className="container my-3" >
			<div className="row">
				<h1>Добавить новость</h1>
				<div className="col-12 col-lg-7 my-3">
					<p>
            Сервис для проверки фейковых новостей. Введите ссылку на новость для проверки, либо текст новости.
          </p>
					<form onSubmit={submitForm}>
						<input
							type="text"
							className="form-control form-control-lg py-3 mb-3"
							name=""
							placeholder="Введите url новости"
							value={newsUrl}
							onChange={changeUrlHandler}
							onFocus={focusUrlHandler}
							onBlur={blurUrlHandler}
							disabled={newsUrlDisabled}
						/>
						{isUrlCorrect
							?  <></>
							: <div className="alert alert-danger" role="alert">* Пожалуйста, введите корректный адрес новости</div>
						}
              <textarea
								cols={40} rows={5}
								className="form-control form-control-lg py-3 mb-3"
								name=""
								placeholder="Введите текст новости"
								value={newsText}
								onChange={changeTextHandler}
								onFocus={focusTextHandler}
								onBlur={blurTextHandler}
								disabled={newsTextDisabled}
							>
							</textarea>
								<input
									type="submit"
									className="button px-5 py-3 btn"
									disabled={buttonDisabled}
									value="Отправить"
								/>
					</form>
				</div>
				<RightBlock/>
			</div>
		</section>
	);
};

export default Form;
