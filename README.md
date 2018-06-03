# emanate

Symlink files from one directory into another directory.

Inspired by [effuse](https://github.com/programble/effuse) and
[stow](https://www.gnu.org/software/stow/manual/stow.html).

## Usage

```
~$ cat ~/.bashrc
cat: /home/pup/.bashrc: No such file or directory
~$ pip install emanate
~$ cd ~/dotfiles
~/dotfiles$ ls -al
drwxr-xr-x.  9 pup pup 4096 Jun  3 12:06 ./
drwx------. 74 pup pup 4096 Jun  3 12:06 ../
drwxr-xr-x.  2 pup pup 4096 Jun  3 11:59 bin/
drwxr-xr-x.  6 pup pup 4096 Jun  3 11:59 .config/
drwxr-xr-x.  8 pup pup 4096 Jun  3 12:10 .git/
-rw-r--r--.  1 pup pup  486 Jun  3 11:59 .bash_aliases
-rw-r--r--.  1 pup pup   78 Jun  3 11:59 .bash_env
-rw-r--r--.  1 pup pup 1987 Jun  3 11:59 .bashrc
-rw-r--r--.  1 pup pup  163 Jun  3 12:06 README.md
~/dotfiles$ cat .bashrc
# TODO: Write .bashrc.
~/dotfiles$ echo '{"ignore": ["README.md"]}' > emanate.json
~/dotfiles$ emanate
~/dotfiles$ cat ~/.bashrc
# TODO: Write .bashrc.
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/duckinator/emanate. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org) code of conduct.

## License

The gem is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).

## Code of Conduct

Everyone interacting in the emanate project’s codebases, issue trackers, chat rooms and mailing lists is expected to follow the [code of conduct](https://github.com/duckinator/emanate/blob/master/CODE_OF_CONDUCT.md).
