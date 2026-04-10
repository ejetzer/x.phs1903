def main():
    from xphs1903.outils.echange import Échange, seldev
    with Échange(seldev()) as ex:
        ex.loop()

if __name__ == '__main__':
    main()
