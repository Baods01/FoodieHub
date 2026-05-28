// 问答接口 - 已合并至 comments.ts 中统一管理
// 提问/回答 API 调用移至 comments.ts 的 QuestionData / AnswerData 相关函数
//
// 保留此文件仅为向前兼容引用，新代码请直接使用 comments.ts

export { fetchQuestions, postQuestion, fetchAnswers, postAnswer } from './comments';
