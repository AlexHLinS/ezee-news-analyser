import axios from "axios";
import {newsData} from "../components/Form";


export default class NewsService {
  static async postNews(news: newsData)  {
    return await axios.post(
      'http://127.0.0.1:8000/',
      {
        'url': news.url,
        'text': news.text
      },
    )
  }
}