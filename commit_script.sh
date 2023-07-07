for file in *; do
  if [ -f "$file" ] && ! [[ $file =~ ^[0-9]+$ ]]; then
    git add "$file"
  fi
done