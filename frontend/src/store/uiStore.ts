import { create } from 'zustand';

interface UiState {
  searchHistory: string[];
  addSearchHistory: (keyword: string) => void;
  clearSearchHistory: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  searchHistory: JSON.parse(localStorage.getItem('searchHistory') || '[]'),
  addSearchHistory: (keyword) =>
    set((state) => {
      const next = [keyword, ...state.searchHistory.filter((k) => k !== keyword)].slice(0, 5);
      localStorage.setItem('searchHistory', JSON.stringify(next));
      return { searchHistory: next };
    }),
  clearSearchHistory: () => {
    localStorage.removeItem('searchHistory');
    return { searchHistory: [] };
  },
}));
