import { environment } from 'environments/environment.dev';

const baseUrl = environment.baseUrl;
export const uriConfig = {
    // User endpoint
    API_USER_LOGIN: baseUrl + '/api/login/',
    API_USER_REGISTER: baseUrl + '/api/register/',
    API_USER_INFOR: baseUrl + '/api/profile/',
    API_FORGET_PASSWORD: baseUrl + '/api/reset-password/',
    API_CONFIRM_PASSWORD: baseUrl + '/api/password-confirm/',
    API_USER_INFOR_UPDATE: baseUrl + '/api/profile/update/',
    API_USER_INFOR_AVATAR: baseUrl + '/api/upload-avatar/',
    API_VERIFY_DOCTOR: baseUrl + '/api/verified_doctor/',
    // ICD-10 endpoint
    API_GET_CHAPTER: baseUrl + '/api/get/chapter/',
    API_GET_BLOCK: baseUrl + '/api/get/block/',
    API_GET_DISEASE: baseUrl + '/api/get/disease/',
    API_GET_ICD10_CHAPTERS: baseUrl + '/api/chapters/',
    API_GET_ICD10_BLOCKS_BY_CHAPTER: (id: number) => 
        baseUrl + `/api/childs/chapter/${id}/`,
    API_GET_ICD10_DISEASES_BY_BLOCK: (id: number) => 
        baseUrl + `/api/childs/block/${id}/`,
    API_GET_ICD10_DISEASES_CHILDREN: (id: number) =>
        baseUrl + `/api/childs/diseases/${id}/`,
    API_GET_ICD10_DATA_CHAPTER: (chapter: string) =>
        baseUrl + `/api/data/chapter/${chapter}/`,
    API_GET_ICD10_DATA_BLOCK: (code: string) =>
        baseUrl + `/api/data/block/${code}/`,
    API_GET_ICD10_DATA_DISEASE: (code: string) =>
        baseUrl + `/api/data/disease/${code}/`,
    API_GET_ICD10_DATA_DISEASE_CHILD: (code: string) =>
        baseUrl + `/api/data/disease_child/${code}/`,
    API_ICD10_SEARCH: baseUrl + '/api/autocomplete',
    // Feedback endpoint
    API_FEEDBACK_CHAPTER_SUBMIT: baseUrl + '/api/feedbacks/chapter/submit/',
    API_FEEDBACK_BLOCK_SUBMIT: baseUrl + '/api/feedbacks/block/submit/',
    API_FEEDBACK_DISEASE_SUBMIT: baseUrl + '/api/feedbacks/disease/submit/',
    API_FEEDBACK_ICD10_LIST: baseUrl + '/api/feedbacks/icd10/user/',
    API_FEEDBACK_CHATBOT_LIST: baseUrl + '/api/feedbacks/chatbot/user/',
    API_FEEDBACK_CHATBOT_SUBMIT: baseUrl + '/api/feedbacks/chatbot/submit/',
    // Notification endpoint
    WEBSOCKET_NOTIFICATIONS: baseUrl.replace('http', 'ws') + '/ws/notifications/',
    API_GET_NOTIFICATIONS: baseUrl + '/api/notifications/user/',
    API_MARK_NOTIFICATION_AS_READ: (id: number) =>
        baseUrl + `/api/notifications/mark_read/${id}/`,
    API_MARK_ALL_NOTIFICATIONS_AS_READ:
        baseUrl + `/api/notifications/mark_all_read/`,
    API_DELETE_NOTIFICATION: (id: number) =>
        baseUrl + `/api/notifications/delete/${id}/`,
    // Chatbot endpoint
    API_GET_CHAT_SESSION: baseUrl + '/api/get_chat_session/',
    API_GET_CHAT_MESSAGES: (id: number) =>
        baseUrl + `/api/get_chat_messages/${id}/`,
    API_CHAT_WITH_AI: baseUrl + '/api/chat_with_ai/',
    WEBSOCKET_CHATBOTS: baseUrl.replace('http', 'ws') + '/ws/ai-stream/',
}