export interface Disease {
    id: number;
    code: string;
    code_no_sign: string;
    title_vi: string;
    updated_at: string;
    is_leaf: boolean;
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
}

export interface Chapter {
    id: number;
    code: string;
    title_vi: string;
    description: string;
}

export interface ICDNode {
  id: number;
  code: string;
  title_vi: string;
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