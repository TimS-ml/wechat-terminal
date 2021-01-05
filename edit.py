import tempfile, os


def modify(string):
    EDITOR = os.environ.get('EDITOR', 'vim')
    # string = "Hi~ How are you"
    init_message = string.encode('UTF-8')
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(init_message)
        tf.flush()
        call([EDITOR, tf.name])
        # do the parsing with `tf` using regular File operations.
        # for instance:
        tf.seek(0)
        edited_message = tf.read()
        new_str = (edited_message.decode("utf-8"))
        new_str = new_str.rstrip("\n")
        # print(repr(new_str))
        return new_str


# usage: func2(target_csv).modify_func()
def modify_func(self):
    cprint('Enter word you want to Modify:', 'green', attrs=['bold'])
    x = input()
    if x in self.source.word.values:
        v = self.source.loc[self.source.word == x]
        cprint(display(v[self.col[0]]), 'red', attrs=['bold', 'underline'])
        for col in self.col[1:]:
            cprint(col, 'magenta', attrs=['underline'])
            print(display(v[col]))
        print('\n')

        print(cfg.col)
        mod = input(
            'Modify?(input number to modify specific column)\n') or ''
        if mod == 'n' or mod == 'N':
            return
        elif mod.isnumeric():
            while mod != 'q':
                mod_col = cfg.col[int(mod)]
                cprint('\nModify ' + mod_col + ' as:',
                       'red',
                       attrs=['bold', 'underline'])
                temp_str = modify(str(v[mod_col].values[0]))
                print(repr(temp_str))
                confirm_mod = input(
                    'Confirm? (n to reinput, q to exit)\n') or ''
                if confirm_mod == 'n' or confirm_mod == 'N':
                    return
                elif confirm_mod == 'q':
                    return
                else:
                    self.source.loc[self.source.word == x,
                                    mod_col] = temp_str
                    csv_dir = '/inputs/'
                    self.source.to_csv(cfg.PATH + csv_dir + cfg.out_name,
                                       index=False,
                                       encoding='utf-8')
                    cprint('Done!', 'white', 'on_magenta', attrs=['bold'])
                    return
        else:
            print('wrong input!')
