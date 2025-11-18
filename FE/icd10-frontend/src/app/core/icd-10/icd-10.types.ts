export interface Disease {
    id: number;
    code: string;
    code_no_sign: string;
    title_vi: string;
    updated_at: string;
    is_leaf: boolean;
    level: number;
}

export interface DiseaseExtraInfo {
    id: number;
    description: string;
    symptoms: string;
    wikipedia_url: string;
    image_url: string;
    
}

export interface Block {
    id: number;
    code: string;
    title_vi: string;
    description: string;
    is_leaf: boolean;
    level: number;
}

export interface Chapter {
    id: number;
    chapter: string;
    code: string;
    title_vi: string;
    description: string;
    is_leaf: boolean;
    level: number;
}

export interface ICDNode {
  id: number;
  code: string;
  title_vi: string;
  is_leaf: boolean;
  level: 'chapter' | 'block' | 'disease' | 'disease_child';
  children?: ICDNode[];
}

export interface FlatNode {
  expandable: boolean;
  code: string;
  title_vi: string;
  level: number;
  data: ICDNode;
}

export class DynamicFlatNode {
    constructor(
        public id: number,
        public chapter: string | null,
        public code: string,
        public title_vi: string,
        public is_leaf: boolean,
        public level: number,
        public expandable: boolean,
        public isLoading = false
    ) {}
}
