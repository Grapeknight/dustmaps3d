import argparse
import time
import pandas as pd
from multiprocessing import cpu_count
from .core import dustmaps3d_from_df

def main():
    """Main function for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Calculate 3D dust properties for a large dataset using dustmaps3d.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_file",
        help="Path to the input data file (e.g., input.csv)."
    )
    parser.add_argument(
        "output_file",
        help="Path to save the output file with results (e.g., output.csv)."
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=8,
        help="Number of CPU threads to use for parallel processing. \nDefault is 8. Use -1 to use all available cores."
    )
    parser.add_argument("--l_col", default="l", help="Name of the Galactic longitude column. Default: 'l'.")
    parser.add_argument("--b_col", default="b", help="Name of the Galactic latitude column. Default: 'b'.")
    parser.add_argument("--d_col", default="d", help="Name of the distance (kpc) column. Default: 'd'.")
    
    args = parser.parse_args()

    # 处理线程数
    if args.threads == -1:
        n_process = cpu_count()
    else:
        n_process = args.threads

    print(f"--- dustmaps3d Batch Processor ---")
    print(f"Input file: {args.input_file}")
    print(f"Output file: {args.output_file}")
    print(f"Using {n_process} threads.")
    
    start_time = time.time()

    try:
        # 读取输入文件
        print(f"\n[1/3] Reading input file...")
        if args.input_file.lower().endswith('.csv'):
            df = pd.read_csv(args.input_file)
        # 添加对FITS的支持
        elif args.input_file.lower().endswith(('.fits', '.fit')):
            from astropy.table import Table
            df = Table.read(args.input_file).to_pandas()
        else:
            raise ValueError("Unsupported file format. Please use a .csv file.")
        
        print(f"Found {len(df)} rows to process.")

        # 调用核心处理函数
        print("\n[2/3] Calculating dust properties...")
        result_df = dustmaps3d_from_df(
            df, 
            l_col=args.l_col, 
            b_col=args.b_col, 
            d_col=args.d_col, 
            n_process=n_process
        )

        # 保存输出文件
        print("\n[3/3] Saving results...")
        if args.output_file.lower().endswith('.csv'):
            result_df.to_csv(args.output_file, index=False)
        elif args.output_file.lower().endswith(('.fits', '.fit')):
            from astropy.table import Table
            out_table = Table.from_pandas(result_df)
            out_table.write(args.output_file, overwrite=True)
        else:
             raise ValueError("Unsupported output format. Please use a .csv file.")

        end_time = time.time()
        print("\n--- Success! ---")
        print(f"Output saved to {args.output_file}")
        print(f"Total time taken: {end_time - start_time:.2f} seconds.")

    except Exception as e:
        print(f"\n--- An error occurred ---")
        print(f"Error: {e}")
        return 1  # Exit with error code

if __name__ == '__main__':
    main()