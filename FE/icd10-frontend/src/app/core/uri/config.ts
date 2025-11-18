import { environment } from 'environments/environment.dev';
import { environment as devenv } from 'environments/environment.dev';

const baseUrl = environment.baseUrl;
const baseUrlDev = devenv.baseUrl;
export const uriConfig = {
    API_USER_LOGIN: baseUrl + '/api/login/',
    API_USER_REGISTER: baseUrl + '/api/register/',
    API_USER_INFOR: baseUrl + '/api/profile/',
    API_FORGET_PASSWORD: baseUrl + '/api/reset-password/',
    API_CONFIRM_PASSWORD: baseUrl + '/api/password-confirm/',
    API_GET_ICD10_CHAPTERS: baseUrl + '/api/chapters/',
    API_GET_ICD10_BLOCKS_BY_CHAPTER: (id: number) => 
        baseUrl + `/api/childs/chapter/${id}/`,
    API_GET_ICD10_DISEASES_BY_BLOCK: (id: number) => 
        baseUrl + `/api/childs/block/${id}/`,
    API_GET_ICD10_DISEASES_CHILDREN: (id: number) =>
        baseUrl + `/api/childs/diseases/${id}/`,
    API_GET_ICD10_DATA_CHAPTER: (id: number) =>
        baseUrl + `/api/data/chapter/${id}/`,
    API_GET_ICD10_DATA_BLOCK: (id: number) =>
        baseUrl + `/api/data/block/${id}/`,
    API_GET_ICD10_DATA_DISEASE: (id: number) =>
        baseUrl + `/api/data/disease/${id}/`,
    API_GET_ICD10_DATA_DISEASE_CHILD: (id: number) =>
        baseUrl + `/api/data/disease_child/${id}/`,
    API_FEEDBACK_ICD10_SUBMIT: baseUrl + '/api/feedbacks/icd10/submit/',
    API_FEEDBACK_ICD10_LIST: baseUrl + '/api/feedbacks/icd10/user/',
}