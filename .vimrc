" Vim/Neovim configuration for weather-tool
" Place this in ~/.vimrc or ~/.config/nvim/init.vim

" Python-specific settings
autocmd FileType python setlocal
    \ tabstop=4
    \ softtabstop=4
    \ shiftwidth=4
    \ textwidth=88
    \ expandtab
    \ autoindent
    \ smartindent
    \ colorcolumn=88

" Black formatter integration
autocmd FileType python nnoremap <leader>f :!black %<CR>
autocmd FileType python nnoremap <leader>F :!black --check %<CR>

" isort integration
autocmd FileType python nnoremap <leader>i :!isort --profile=black %<CR>
autocmd FileType python nnoremap <leader>I :!isort --check-only --profile=black %<CR>

" flake8 integration
autocmd FileType python nnoremap <leader>l :!flake8 %<CR>

" mypy integration
autocmd FileType python nnoremap <leader>m :!mypy %<CR>

" Format on save (optional)
" autocmd BufWritePre *.py :!black %
" autocmd BufWritePre *.py :!isort --profile=black %

" Key mappings
let mapleader = " "
nnoremap <leader>ff :!python dev.py format<CR>
nnoremap <leader>ll :!python dev.py lint<CR>
nnoremap <leader>tt :!python dev.py test<CR>
