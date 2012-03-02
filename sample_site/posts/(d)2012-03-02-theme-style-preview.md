title: Theme Style Preview
timestamp: 2012-03-02 10:49:00
status: draft
slug: theme-style-preview


---

This is a sample post that illustrates all of the styles the current Engineer theme uses.

---

# First-level Heading

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus lacus risus, feugiat vitae fermentum non, vulputate sit amet sem. Cras a leo a eros pharetra consequat vitae at tortor. Praesent non nibh vitae quam dignissim pulvinar sit amet a est. Donec blandit justo quis neque aliquam a suscipit massa egestas. Morbi porttitor nisi lorem.

## Second-level Heading

Etiam sit amet congue neque. Suspendisse vitae lectus sit amet neque dignissim pulvinar in quis neque. Sed luctus hendrerit lacus, a facilisis velit tincidunt id. Sed eu sem nibh. Ut dictum semper dui. Morbi in massa ac eros fringilla aliquam. Donec fringilla blandit commodo. Morbi placerat convallis nisl, sit amet laoreet turpis sodales auctor.

* Ichi
* Ni
* San
* Yon

In quis turpis lacus, sit amet venenatis metus. Cras massa leo, aliquet vel pellentesque vel, luctus nec lectus. Nunc sit amet mauris in nisi faucibus tempor sit amet viverra erat. Maecenas dignissim imperdiet pretium. Nunc vehicula nibh a tortor hendrerit imperdiet. Phasellus a nisl sit amet sem dapibus tincidunt accumsan a velit.

1. Wan
2. Tu
3. Tri
4. Fo
5. Faiv

## Some Sample Code Highlighting

### HTML

	:::html
	<section class="three columns" id="sidebar">
		<p class="replace_me">You should customize the 
		sidebar content.</p>
		<p class="replace_me">You can do this by adding a 
			'theme/_sidebar.html' template to your 
			templates directory.</p>
	</section>

### Python

    :::python
    def cmdline(args=sys.argv):
        # Common parameters
        common_parser = argparse.ArgumentParser(add_help=False)
        common_parser.add_argument('--no-cache', '-n', dest='disable_cache', action='store_true',
                                   help="Disable the post cache.")
        common_parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Display verbose output.")
        common_parser.add_argument('--config', dest='config_file', default='config.yaml',
                                   help="Specify a configuration file to use.")
    
        main_parser = argparse.ArgumentParser(
            description="Engineer site builder.",
            parents=[common_parser])
    
        top_group = main_parser.add_mutually_exclusive_group(required=True)
        top_group.add_argument('--build', '-b', dest='build',
                               action='store_true', help="Build the site.")
        top_group.add_argument('--serve', '-s', dest='serve',
                               action='store_true', help="Start the development server.")
        top_group.add_argument('--clean', '-c', dest='clean',
                               action='store_true', help="Clean the output directory.")
    
        args = main_parser.parse_args()
    
        settings.initialize_from_yaml(args.config_file)
        settings.DISABLE_CACHE = args.disable_cache
    
        if args.verbose:
            import logging
    
            logger.setLevel(logging.DEBUG)
    
        if args.serve:
            #from engineer.server import serve
    
            #serve()
            management_server()
        elif args.build:
            build()
            exit()
        elif args.clean:
            clean()
            exit()
        else:
            main_parser.print_help()
            exit()