export interface Account {
  id: number;
  user: number;
  name: string;
  balance: number;
  currency: string;
  type: string;
  deleted: boolean;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
}